
subroutine PROBINIT (init,name,namlen,problo,probhi)

  use probdata_module
  use network, only : network_init
!  use eos_module
  use fundamental_constants_module, only : c_light, a_rad
  implicit none

  integer init, namlen
  integer name(namlen)
  double precision problo(1), probhi(1)
  
  integer untin,i
  
  namelist /fortin/ &
       denerr,   dengrad,  max_denerr_lev,  max_dengrad_lev, &
       velerr,   velgrad,  max_velerr_lev,  max_pressgrad_lev, &
       presserr, pressgrad,max_presserr_lev,max_pressgrad_lev, &
       temperr,  tempgrad, max_temperr_lev, max_tempgrad_lev, &
       raderr,   radgrad,  max_raderr_lev,  max_radgrad_lev
  
  !
  !     Build "probin" filename -- the name of file containing fortin namelist.
  !     
  integer maxlen
  parameter (maxlen=256)
  character probin*(maxlen)
  
  call network_init()
  
  if (namlen .gt. maxlen) then
     write(6,*) 'probin file name too long'
     stop
  end if
  
  do i = 1, namlen
     probin(i:i) = char(name(i))
  end do
  
  ! set namelist defaults
  x0 = 0.5d0
  tau0 = 10.0d0
  Q = 1.d0
  Temp0 = 1.d6
  kapbar = 1.d0
  epsilon = 1.d0
  p0 = 0.5d0
  p1 = 0.5d0

  denerr = 1.d20
  dengrad = 1.d20
  max_denerr_lev = -1
  max_dengrad_lev = -1
  
  velerr = 1.d20
  velgrad = 1.d20
  max_velerr_lev = -1
  max_velgrad_lev = -1
  
  presserr = 1.d20
  pressgrad = 1.d20
  max_presserr_lev = -1
  max_pressgrad_lev = -1
  
  temperr = 1.d20
  tempgrad = 1.d20
  max_temperr_lev = -1
  max_tempgrad_lev = -1
  
  raderr = 1.d20
  radgrad = 1.d20
  max_raderr_lev = -1
  max_radgrad_lev = -1
  
  center(1) = (problo(1)+probhi(1))/2.d0
  xmin = problo(1)
  xmax = probhi(1)

  ! Read namelists
  untin = 9
  open(untin,file=probin(1:namlen),form='formatted',status='old')
  read(untin,fortin)
  close(unit=untin)
  
  t0 = tau0 / (epsilon*c_light*kapbar)
  x0 = x0 / kapbar
  qn(0) = a_rad * Temp0**4 * c_light * kapbar * Q * p0
  qn(1) = a_rad * Temp0**4 * c_light * kapbar * Q * p1

end subroutine PROBINIT

! ::: -----------------------------------------------------------
! ::: This routine is called at problem setup time and is used
! ::: to initialize data on each grid.  
! ::: 
! ::: NOTE:  all arrays have one cell of ghost zones surrounding
! :::        the grid interior.  Values in these cells need not
! :::        be set here.
! ::: 
! ::: INPUTS/OUTPUTS:
! ::: 
! ::: level     => amr level of grid
! ::: time      => time at which to init data             
! ::: lo,hi     => index limits of grid interior (cell centered)
! ::: nstate    => number of state components.  You should know
! :::		   this already!
! ::: state     <=  Scalar array
! ::: delta     => cell size
! ::: xlo,xhi   => physical locations of lower left and upper
! :::              right hand corner of grid.  (does not include
! :::		   ghost region).
! ::: -----------------------------------------------------------
subroutine ca_initdata(level,time,lo,hi,nscal, &
     state,state_l1,state_h1, &
     delta,xlo,xhi)
  use probdata_module
  use meth_params_module, only : NVAR, URHO, UMX, UMY, UEDEN, UEINT, UFS, UFX, UTEMP
  use network, only : nspec, naux
  use eos_module, only : eos_given_RTX
  use fundamental_constants_module, only : k_B, a_rad
  
  implicit none
  
  integer :: level, nscal
  integer :: lo(1), hi(1)
  integer :: state_l1,state_h1
  double precision :: state(state_l1:state_h1,NVAR)
  double precision :: time, delta(1)
  double precision :: xlo(1), xhi(1)
  
  integer :: i
  double precision :: c_v, eint

  do i = lo(1), hi(1)
  
     state(i,URHO) = 1.0
     state(i,UTEMP) = 0.0
     state(i,UMX) = 0.0
        
     ! set the composition to be all in the first species
     state(i,UFS:UFS-1+nspec) = 0.d0
     state(i,UFS  ) = state(i,URHO)
     if (naux > 0) then
        state(i,UFX) = state(i,URHO)
     end if
     
     state(i,UEINT) = 0.0
     state(i,UEDEN) = 0.0

  enddo
  
end subroutine ca_initdata


! ::: 
! ::: -----------------------------------------------------------
! :::
subroutine ca_initrad(level,time,lo,hi,nrad, &
     rad_state,rad_state_l1, &
     rad_state_h1, &
     delta,xlo,xhi)

  use probdata_module
  use fundamental_constants_module, only: a_rad
  
  implicit none
  integer :: level, nrad
  integer :: lo(1), hi(1)
  integer :: rad_state_l1,rad_state_h1
  double precision :: xlo(1), xhi(1), time, delta(1)
  double precision ::  rad_state(rad_state_l1:rad_state_h1, nrad)

  ! local variables
  integer :: i,j
             
  do i = lo(1), hi(1)
     rad_state(i,:) = 0.0
  enddo
        
end subroutine ca_initrad


! ::: -----------------------------------------------------------

      subroutine ca_hypfill(adv,adv_l1,adv_h1, &
          domlo,domhi,delta,xlo,time,bc)

      use meth_params_module, only : NVAR

      implicit none

      include 'bc_types.fi'
      integer adv_l1,adv_h1
      integer bc(1,2,*)
      integer domlo(1), domhi(1)
      double precision delta(1), xlo(1), time
      double precision adv(adv_l1:adv_h1,NVAR)

      integer n

      do n = 1,NVAR
         call filcc(adv(adv_l1,n),adv_l1,adv_h1, &
             domlo,domhi,delta,xlo,bc(1,1,n))
      enddo

      end

! ::: 
! ::: -----------------------------------------------------------
! :::

      subroutine ca_denfill(adv,adv_l1,adv_h1, &
          domlo,domhi,delta,xlo,time,bc)
      implicit none
      include 'bc_types.fi'
      integer adv_l1,adv_h1
      integer bc(1,2,*)
      integer domlo(1), domhi(1)
      double precision delta(1), xlo(1), time
      double precision adv(adv_l1:adv_h1)

      call filcc(adv,adv_l1,adv_h1,domlo,domhi,delta,xlo,bc)

      end

! ::: 
! ::: -----------------------------------------------------------
! :::

      subroutine ca_radfill(adv,adv_l1,adv_h1, &
          domlo,domhi,delta,xlo,time,bc)
      implicit none
      include 'bc_types.fi'
      integer adv_l1,adv_h1
      integer bc(1,2,*)
      integer domlo(1), domhi(1)
      double precision delta(1), xlo(1), time
      double precision adv(adv_l1:adv_h1)

      call filcc(adv,adv_l1,adv_h1,domlo,domhi,delta,xlo,bc)

      end
      
!-----------------------------------------------------------------------
